import math

import requests

from config import GOOGLE_API_KEY


def get_coordinates(zip_code):
    url = "https://maps.googleapis.com/maps/api/geocode/json"

    params = {"address": zip_code, "key": GOOGLE_API_KEY}

    response = requests.get(url, params=params)

    data = response.json()

    location = data["results"][0]["geometry"]["location"]

    latitude = location["lat"]
    longitude = location["lng"]

    return latitude, longitude


def search_businesses(latitude, longitude, radius_miles, query):
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.nationalPhoneNumber,"
            "places.websiteUri,"
            "places.rating,"
            "places.userRatingCount,"
            "places.googleMapsUri,"
            "places.location,"
            "places.businessStatus"
        ),
    }

    if radius_miles < 20:
        search_radii = [10]
    else:
        search_radii = [10, radius_miles]

    combined_places = {}

    for search_radius in search_radii:
        radius_meters = search_radius * 1609.34

        body = {
            "textQuery": query,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": radius_meters,
                }
            },
        }

        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()

        data = response.json()
        print(
            f"{search_radius}-mile bias returned {len(data.get('places', []))} places"
        )
        places = data.get("places", [])

        for place in places:
            print(place["displayName"]["text"])
            combined_places[place["id"]] = place

    return {"places": list(combined_places.values())}


def build_results(businesses, user_lat, user_lng, radius_miles):
    results = []
    for business in businesses["places"]:
        bus_lat = business["location"]["latitude"]
        bus_lng = business["location"]["longitude"]
        distance = calculate_distance(user_lat, user_lng, bus_lat, bus_lng)
        if distance > radius_miles +5:
            continue
        results.append(
            {
                "name": business["displayName"]["text"],
                "address": business.get("formattedAddress"),
                "phone": business.get("nationalPhoneNumber"),
                "website": business.get("websiteUri"),
                "rating": business.get("rating"),
                "reviews": business.get("userRatingCount"),
                "distance (mi)": round(distance, 2),
            }
        )

    return results


def calculate_distance(user_lat, user_lng, bus_lat, bus_lng):
    earth_radius_miles = 3958.8

    user_lat = math.radians(user_lat)
    user_lng = math.radians(user_lng)
    business_lat = math.radians(bus_lat)
    business_lng = math.radians(bus_lng)

    lat_diff = business_lat - user_lat
    lng_diff = business_lng - user_lng

    a = (
        math.sin(lat_diff / 2) ** 2
        + math.cos(user_lat) * math.cos(business_lat) * math.sin(lng_diff / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius_miles * c


def rank_results(results):
    C = 4.5
    m = 100

    for b in results:
        R = b["rating"] or 0
        v = b["reviews"] or 0

        if v == 0:
            b["score"] = 0
        else:
            bayesian = (v / (v + m)) * R + (m / (v + m)) * C
            review_bonus = 0.03 * math.log10(v)
            b["score"] = bayesian + review_bonus

    results.sort(key=lambda b: b["score"], reverse=True)
    return results


def find_service_pros(zip_code, radius, profession):
    user_lat, user_lng = get_coordinates(zip_code)
    businesses = search_businesses(user_lat, user_lng, radius, profession)
    results = build_results(businesses, user_lat, user_lng, radius)

    results = rank_results(results)

    return results
