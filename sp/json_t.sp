import "json"

obj := {"a"=1,"b"=2,"c"=[3, 4, 5]};

json.writeFile(obj, "json_test.json");
