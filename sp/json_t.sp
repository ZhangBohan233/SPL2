import "json"

obj := {"a"=1,"b"=2,"c"=[3, 4, 5]};

json.write_file(obj, "json_test.json");
