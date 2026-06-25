from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests


TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"
LIST_FOLDER_URL = "https://api.dropboxapi.com/2/files/list_folder"
LIST_FOLDER_CONTINUE_URL = "https://api.dropboxapi.com/2/files/list_folder/continue"
GET_SHARED_LINK_FILE_URL = "https://content.dropboxapi.com/2/sharing/get_shared_link_file"
REQUEST_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class DropboxFile:
    id: str
    name: str
    path_display: str
    server_modified: str
    rev: str
    size: int


def canonicalize_shared_link_url(shared_link_url: str) -> str:
    normalized = str(shared_link_url or "").strip()
    if not normalized:
        return ""

    parsed = urlsplit(normalized)
    if "dropbox.com" not in parsed.netloc.lower():
        return normalized

    dl_value = "0"
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() == "dl" and value:
            dl_value = value

    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode({"dl": dl_value}), ""))


def refresh_access_token(app_key: str, app_secret: str, refresh_token: str) -> str:
    response = requests.post(
        TOKEN_URL,
        auth=(app_key, app_secret),
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Dropbox token refresh failed ({response.status_code}): {response.text}")

    payload = response.json()
    access_token = payload.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError("Dropbox token refresh succeeded without an access_token.")
    return access_token


def list_shared_folder_files(access_token: str, shared_link_url: str) -> list[DropboxFile]:
    shared_link = canonicalize_shared_link_url(shared_link_url)
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    pending_paths = [""]
    files: list[DropboxFile] = []

    while pending_paths:
        current_path = pending_paths.pop(0)
        payload = _post_json(
            LIST_FOLDER_URL,
            headers=headers,
            json_body={
                "path": current_path,
                "recursive": False,
                "include_deleted": False,
                "shared_link": {"url": shared_link},
            },
        )
        _collect_entries(payload, current_path, files, pending_paths)

        while payload.get("has_more"):
            payload = _post_json(
                LIST_FOLDER_CONTINUE_URL,
                headers=headers,
                json_body={"cursor": payload["cursor"]},
            )
            _collect_entries(payload, current_path, files, pending_paths)

    return files


def filter_audio_files(files: list[DropboxFile], include_regex: str) -> list[DropboxFile]:
    pattern = re.compile(include_regex, re.IGNORECASE) if include_regex else None
    allowed_suffixes = {".mp3", ".wav", ".m4a"}

    filtered = [
        file
        for file in files
        if Path(file.name).suffix.lower() in allowed_suffixes
        and (pattern is None or pattern.search(file.path_display))
    ]

    return sorted(filtered, key=lambda file: file.server_modified, reverse=True)


def select_candidate(files: list[DropboxFile], *, dropbox_path: str | None = None) -> DropboxFile:
    if dropbox_path:
        normalized = dropbox_path.strip().lower()
        for file in files:
            if file.path_display.lower() == normalized:
                return file
        raise ValueError(f"Dropbox path was not found in eligible files: {dropbox_path}")

    if not files:
        raise ValueError("No eligible Dropbox audio files found.")
    return files[0]


def download_file_from_shared_link(
    access_token: str,
    shared_link_url: str,
    file_path_in_folder: str,
    local_save_path: str | Path,
) -> Path:
    shared_link = canonicalize_shared_link_url(shared_link_url)
    target_path = Path(local_save_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": json.dumps({"url": shared_link, "path": file_path_in_folder}),
    }

    response = requests.post(
        GET_SHARED_LINK_FILE_URL,
        headers=headers,
        stream=True,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Dropbox download failed ({response.status_code}): {response.text}")

    with target_path.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                handle.write(chunk)
    return target_path


def safe_local_audio_path(file: DropboxFile, download_dir: str | Path = "downloads") -> Path:
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "_", file.id.replace("id:", "id_", 1)).strip("_")
    safe_name = re.sub(r"[^A-Za-z0-9 ._-]+", "_", file.name).strip()
    return Path(download_dir) / f"{safe_id}__{safe_name}"


def _post_json(url: str, *, headers: dict, json_body: dict, attempts: int = 4) -> dict:
    for attempt in range(attempts):
        response = requests.post(
            url,
            headers=headers,
            json=json_body,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code < 400:
            return response.json()
        if response.status_code not in {429, 500, 502, 503} or attempt == attempts - 1:
            raise RuntimeError(f"Dropbox API failed ({response.status_code}): {response.text}")
        time.sleep(2**attempt)
    raise RuntimeError("Dropbox API failed after retry exhaustion.")


def _collect_entries(payload: dict, current_path: str, files: list[DropboxFile], pending_paths: list[str]) -> None:
    for entry in payload.get("entries", []):
        tag = entry.get(".tag")
        name = entry.get("name", "")
        path_display = entry.get("path_display")
        if not path_display:
            path_display = f"/{name}" if current_path in {"", "/"} else f"{current_path.rstrip('/')}/{name}"

        if tag == "file":
            files.append(
                DropboxFile(
                    id=entry["id"],
                    name=name,
                    path_display=path_display,
                    server_modified=entry.get("server_modified", ""),
                    rev=entry.get("rev", ""),
                    size=int(entry.get("size", 0)),
                )
            )
        elif tag == "folder":
            pending_paths.append(path_display)
