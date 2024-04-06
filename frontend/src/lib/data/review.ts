import { baseApiUrl, token } from "."

const reviewApiUrl = `${baseApiUrl}/meeting/rate_meeting`
export async function leaveReview(id: string, rating: number, comment: string) {
    await fetch(`${reviewApiUrl}/${id}`, {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "oauth-token": token(),
        },
        body: JSON.stringify({
            rating,
            comment_rating: comment,
        }),
    })
}
