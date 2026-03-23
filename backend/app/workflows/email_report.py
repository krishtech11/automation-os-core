def run(config):

    email = config.get("email", "user@example.com")

    return {
        "status": "success",
        "message": f"Report sent to {email}"
    }