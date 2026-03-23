def run(config):

    folder = config.get("folder", "documents")

    return {
        "status": "success",
        "message": f"Documents summarized in {folder}"
    }