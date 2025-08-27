import asyncio
import json
import pathlib

import pydantic_settings
from gamer_x.agent import main


class CapsuleParameters(pydantic_settings.BaseSettings):
    prompt: str
    expected_results: str | list[str] | None = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        *args,
        **kwargs,
    ):
        # the order of the sources is what defines the priority (highest to lowest):
        # - the first source that contains a value for a field is used
	    # - defaults are used if no source contains a value (or exception raised if no default)
        return (
            init_settings,
            pydantic_settings.sources.JsonConfigSettingsSource(settings_cls, json_file='params.json'),
            pydantic_settings.CliSettingsSource(settings_cls, cli_parse_args=True),	    
        )

if __name__ == "__main__": 
    params = CapsuleParameters()
    print(params)

    response = asyncio.run(main(params.prompt))

    print("Got response:\n", response)

    if params.expected_results:
        data = []
        if isinstance(params.expected_results, str):
            params.expected_results = [params.expected_results]
        for result in params.expected_results:
            # TODO use an LLM API to evaluate this instead of just checking presence
            data.append({
                'expected_result': result,
                'is_in_response': result in str(response), # TODO check relevant keys in response
            })
        pathlib.Path('/root/capsule/results/expected_results.json').write_text(json.dumps(data, indent=4))
