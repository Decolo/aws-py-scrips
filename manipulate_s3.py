import asyncio
from bs4 import BeautifulSoup
import s3_utils

def delete_file_with_prefix(delete_items):
    try:
        for item in delete_items:
            if item is None:
                continue

            s3_utils.delete_file(item)

            print("Deleted: " + item)

        return True
    except ValueError as e:
        print(e)
        return False

def modify_each_file(delete_items):

    try:
        for item in delete_items:
            if item is None:
                continue

            file_content = s3_utils.get_file_content(item)

            soup = BeautifulSoup(file_content, "html.parser")

            for p in soup.find_all("p"):
                if p.find("a", class_="l8editor-forum"):
                    p.decompose()

            modified_content = str(soup)

            s3_utils.modify_file(item, modified_content)

            print("Modified: " + item + "\n")

        return True
    except ValueError as e:
        print(e)
        return False

async def run():
    all_items = s3_utils.list_all_files()

    modify_each_file(all_items)

asyncio.run(run())
