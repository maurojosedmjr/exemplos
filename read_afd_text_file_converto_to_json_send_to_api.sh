#!/bin/bash
json_objects=()

while read line;
do 
	if [ ${#line} -ne 35 ]; then
		continue
	fi
	echo $line
	line_type=${line:9:1}
	if [ $line_type == "3" ]; then
		nsr=${line:0:9}
		punchtime=${line:10:12}
		pis=$(echo ${line:22:34} | sed 's/\r$//')
		if [[ $pis = 0* ]]; then
			echo "=============================================="
			echo $nsr
			echo $punchtime
			echo $pis
			echo "=============================================="
			json_object=$(jq -n --arg key1 "nsr" --arg val1 "${nsr}" \
	                    --arg key2 "punchtime" --arg val2 "${punchtime}" \
	                    --arg key3 "pis" --arg val3 "${pis}" \
	                    '{($key1): $val1, ($key2): $val2, ($key3): $val3}')
			json_objects+=("$json_object")
		fi
	fi
done < afd.txt

json_array=$(jq -s '.' <<< "${json_objects[@]}")
# echo "$json_array"

echo "curl -X POST http://0.0.0.0:9090/afd-json -H 'Content-Type: application/json' -H 'Authorization: Bearer any_token_here' -d '${json_array}'"
