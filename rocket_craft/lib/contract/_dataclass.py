from typing import Any, Callable, Union, TypeAlias

Mapping: TypeAlias = dict[str, Union[str, Callable[[Any], Any]]]

def transform(data: dict[str, Any], mapping: Mapping) -> dict[str, Any]:
	mapped_data = dict()
	for k, v in data.items():
		if k in mapping:
			if isinstance(mapping[k], str):
				mapped_data[mapping[k]] = v
			elif isinstance(mapping[k], Callable):
				key, value = mapping[k](v)
				mapped_data[key] = value
	return mapped_data
