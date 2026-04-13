from pystash.plugins.registry import registry
from pystash.plugins.inputs.stdin_input import StdinInput
from pystash.plugins.inputs.file_input import FileInput
from pystash.plugins.inputs.http_input import HttpInput
from pystash.plugins.filters.mutate import MutateFilter
from pystash.plugins.filters.json_filter import JsonFilter
from pystash.plugins.filters.grok_filter import GrokFilter
from pystash.plugins.filters.date_filter import DateFilter
from pystash.plugins.filters.drop_filter import DropFilter
from pystash.plugins.outputs.stdout_output import StdoutOutput
from pystash.plugins.outputs.file_output import FileOutput
from pystash.plugins.outputs.http_output import HttpOutput
from pystash.plugins.outputs.elasticsearch_output import ElasticsearchOutput

registry.register("input", "stdin", StdinInput)
registry.register("input", "file", FileInput)
registry.register("input", "http", HttpInput)
registry.register("filter", "mutate", MutateFilter)
registry.register("filter", "json", JsonFilter)
registry.register("filter", "grok", GrokFilter)
registry.register("filter", "date", DateFilter)
registry.register("filter", "drop", DropFilter)
registry.register("output", "stdout", StdoutOutput)
registry.register("output", "file", FileOutput)
registry.register("output", "http", HttpOutput)
registry.register("output", "elasticsearch", ElasticsearchOutput)
