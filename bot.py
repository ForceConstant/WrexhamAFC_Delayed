import praw
import time
from datetime import datetime, timezone
from config import CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD

# Reddit API credentials
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
    username=USERNAME,
    password=PASSWORD
)

# Source and destination subreddit names
source_subreddit_name = 'WrexhamAFC'
destination_subreddit_name = 'WrexhamAFC_Delayed'

# Function to check if a submission is more than 36 hours old
def is_old_enough(submission_arg):
    """
    Checks if a submission is old enough.

    Args:
        submission (object): The submission object containing the 'created_utc' attribute.

    Returns:
        bool: True if the submission is more than 36 hours old, False otherwise.
    """
    current_time = datetime.utcnow()
    submission_time = datetime.utcfromtimestamp(submission_arg.created_utc)
    time_difference = current_time - submission_time
    return time_difference.total_seconds() > (36 * 60 * 60)

# Function to check if a submission has been crossposted
def is_crossposted(submission):
    """
    Checks if a submission has been crossposted."""

    # print each duplicate
    if hasattr(submission, 'duplicates'):
        # print("Duplicate submissions:")
        for duplicate in submission.duplicates():
            # print(f"Title: {duplicate.title} Subreddit: {duplicate.subreddit}")
            if duplicate.subreddit == destination_subreddit_name:
                # print("Duplicate is in destination subreddit.")
                return True

    return False

# Function to crosspost a submission
def crosspost_submission(submission):
    """
    Crossposts a submission to the destination subreddit."""
    try:
        crossposted_submission = submission.crosspost(subreddit=destination_subreddit_name, title=submission.title)
        lock_comments(crossposted_submission)

        print(f"Crossposted: {submission.title}")
    except Exception as e2:
        print(f"Error while crossposting '{submission.title}': {e2}")

# Function to lock comments on a submission
def lock_comments(submission):
    """
    Locks the comments on a submission.

    Parameters:
    - submission: The submission object to lock the comments on.

    Returns:
    None
    """
    try:
        submission.mod.lock()
        # print(f"Comments locked on: {submission.title}")
    except Exception as e3:
        print(f"Error while locking comments on '{submission.title}': {e3}")

try:
    # Monitor the source subreddit for new submissions
    source_subreddit = reddit.subreddit(source_subreddit_name)
    for submission in source_subreddit.new(limit=20):
        if is_old_enough(submission) and not is_crossposted(submission):
            # print the title of the submission
            # print(f"New submission found: {submission.title}")

            crosspost_submission(submission)

            # Exit application after crossposting the first submission using exit
            time.sleep(5)  # Optional: Add a short delay to avoid rate limiting

except Exception as e:
    print(f"An error occurred: {e}")

print("Done")

