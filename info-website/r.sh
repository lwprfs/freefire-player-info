KEY="pZkWNtS5_6qePyHEC_7zFJes3fvjxh19JjlcoEMaL6I"

# 1. The exact UID from their docs, no region
curl -i -H "x-api-key: $KEY" "https://api.gameskinbo.com/ff-info/get?uid=2312730961"

# 2. Same UID, WITH region=BD
curl -i -H "x-api-key: $KEY" "https://api.gameskinbo.com/ff-info/get?uid=2312730961&region=BD"

# 3. Your UID, no region
curl -i -H "x-api-key: $KEY" "https://api.gameskinbo.com/ff-info/get?uid=2950019597"

# 4. Your UID, region=IND (different region)
curl -i -H "x-api-key: $KEY" "https://api.gameskinbo.com/ff-info/get?uid=2950019597&region=IND"
