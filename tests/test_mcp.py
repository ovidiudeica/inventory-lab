"""Validate both Python tools and the MCP stdio protocol."""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from inventory import mcp_server
from inventory.core import summary, investigate, report


def test_mcp_tools():
    assert mcp_server.get_stock_summary() == summary()
    assert mcp_server.investigate_sku('SKU-101') == investigate('SKU-101')
    assert mcp_server.get_procedure('SOP-01')['title'] == 'Independent recount'
    assert mcp_server.generate_report('SKU-101') == report('SKU-101')


def test_mcp_stdio_round_trip():
    async def exercise():
        params = StdioServerParameters(
            command=sys.executable, args=['-m', 'inventory.mcp_server']
        )
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                initialised = await session.initialize()
                assert initialised.serverInfo.name == 'inventory-lab'
                tools = await session.list_tools()
                assert {tool.name for tool in tools.tools} == {
                    'get_stock_summary', 'investigate_sku',
                    'get_procedure', 'generate_report',
                }
                assert all(tool.annotations and tool.annotations.readOnlyHint is True and tool.annotations.destructiveHint is False for tool in tools.tools)
                for name, args, expected in [
                    ('get_stock_summary', {}, '406.5'),
                    ('investigate_sku', {'sku': 'SKU-101'}, 'Unreconciled transfer'),
                    ('get_procedure', {'procedure_id': 'SOP-01'}, 'Independent recount'),
                    ('generate_report', {'sku': 'SKU-101'}, 'Synthetic data only'),
                ]:
                    result = await session.call_tool(name, arguments=args)
                    assert not result.isError, result
                    assert expected in str(result.model_dump())
                for name, args in [
                    ('investigate_sku', {'sku': 'INVALID'}),
                    ('get_procedure', {'procedure_id': 'INVALID'}),
                    ('generate_report', {'sku': 'INVALID'}),
                ]:
                    result = await session.call_tool(name, arguments=args)
                    assert result.isError, result

    asyncio.run(asyncio.wait_for(exercise(), timeout=30))
