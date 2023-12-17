def truncate_description(description):
    if len(description) > 150:
        return description[:150] + "..."
    return description