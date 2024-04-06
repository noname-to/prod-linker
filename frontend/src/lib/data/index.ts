export const baseApiUrl = "https://api.noname.to"

const tokenKey = "token"
export const token = () => localStorage.getItem(tokenKey) ?? ""
export const updateToken = (t: string) => localStorage.setItem(tokenKey, t)
