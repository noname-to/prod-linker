import type { LngLat } from "@yandex/ymaps3-types"
import booleanPointInPolygon from "@turf/boolean-point-in-polygon"
import { point } from "@turf/helpers"
import moscow from "./regions/moscow"

const regions = [moscow]

export function isInDeliveryZone(coordinates: LngLat) {
    const p = point([coordinates[0], coordinates[1]])
    return regions.some((r) => r.features.some((poly) => booleanPointInPolygon(p, poly)))
}
