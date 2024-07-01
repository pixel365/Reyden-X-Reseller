export const twitchChannelUrlValidator = (id: number): boolean => {
    return id > 0
}

export const youtubeChannelUrlValidator = (url: string): boolean => {
    const patterns: string[] = [
        "https:\/\/www\.youtube\.com\/\@[a-zA-Z_]+$",
        "https:\/\/www\.youtube\.com\/channel\/[a-zA-Z\d_]+$",
    ]

    for (let i = 0; i < patterns.length; i++) {
        const m = url.match(patterns[i])
        if (m != null){
            if (m.length > 0)
                return true
        }
    }

    return false
}
