import uvicorn


def main() -> None:
    uvicorn.run("upload_api.app:app", host="127.0.0.1", port=8002, reload=True)


if __name__ == "__main__":
    main()
