from serviceprofinder import find_service_pros

zip_code = input("Enter ZIP code: ")
radius = int(input("Enter radius (miles): "))
profession = input("Enter profession: ")
# zip_code = 20148
# radius = 10
# profession = "HVAC"

results = find_service_pros(zip_code, radius, profession)
for business in results:
    print(f"Name: {business['name']}")
    print(f"Address: {business['address']}")
    print(f"Phone: {business['phone']}")
    print(f"Website: {business['website']}")
    print(f"Rating: {business['rating']}")
    print(f"Reviews: {business['reviews']}")
    print(f"Status: {business['status']}")
    print("-" * 50)