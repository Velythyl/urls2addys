_STR_FAILED_TO_GET = "Failed to get address from Google Maps"
_ERR_MSGs = []
def get_address(placename_url):
    place, url = placename_url

    def _get():
        import re
        import subprocess
        page = subprocess.check_output(["curl", url], universal_newlines=True)
        PATTERN = f'<meta content=".+ · (.+?)" property="og:title">'
        regex = re.search(pattern=PATTERN, string=page).groups()
        return f"{regex[0]}"

    try:
        ret = _get()
    except:
        _ERR_MSGs.append(f"Something went wrong with this place: {place}\nThis corresponds to this url: {url}\n")
        ret = _STR_FAILED_TO_GET

    return [ret]


def main(CSV_PATH, INDEX_COLUMN_NAME, LINK_COLUMN_NAME, TAG_COLUMN_NAME=None):
    import pandas as pd
    file = pd.read_csv(CSV_PATH).set_index(INDEX_COLUMN_NAME).fillna('empty field')

    urls = file[LINK_COLUMN_NAME].values.tolist()
    places = file.index.values.tolist()
    addys = list(map(get_address, zip(places,urls)))

    file[["Address"]] = addys
    file = file.loc[file["Address"] != _STR_FAILED_TO_GET]

    print()
    list(map(print, _ERR_MSGs))
    if len(_ERR_MSGs) > 0:
        print("None of the failed URLs were emitted to the output CSVs.\n")

    if TAG_COLUMN_NAME is None:
        save_path = CSV_PATH.split(".")
        save_path = save_path[0] + "_DONE.csv"
        file.to_csv(save_path)
    else:
        __tags = file[[TAG_COLUMN_NAME]].values.tolist()
        for _tags in __tags:
            assert len(_tags) == 1
            data = file.loc[file[TAG_COLUMN_NAME] == _tags[0]]
            data.to_csv(f"{_tags[0]}.csv")

    print("Done!")

if __name__ == '__main__':
    main("table.csv", "Name", "Google Maps link", TAG_COLUMN_NAME="Category")
