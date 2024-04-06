import { type AddressSuggestion } from "$lib/data/addresses"

export function debounce<P>(callee: (...args: P[]) => void, timeoutMs: number) {
    let lastCall: number
    let lastCallTimer: number
    return function perform(...args: P[]) {
        const previousCall = lastCall
        lastCall = Date.now()
        if (previousCall && lastCall - previousCall <= timeoutMs) {
            clearTimeout(lastCallTimer)
        }
        lastCallTimer = setTimeout(() => callee(...args), timeoutMs)
    }
}

export function suggestionToAddress(suggestion: AddressSuggestion): string {
    return [
        suggestion.data.region_with_type,
        suggestion.data.city != suggestion.data.region ? suggestion.data.city_with_type : null,
        suggestion.data.area_with_type,
        suggestion.data.settlement_with_type,
        suggestion.data.street_with_type,
        suggestion.data.house ? `${suggestion.data.house_type} ${suggestion.data.house}` : null,
        suggestion.data.block ? `${suggestion.data.block_type} ${suggestion.data.block}` : null,
    ]
        .filter((x) => !!x)
        .join(", ")
}
