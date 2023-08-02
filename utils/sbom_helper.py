"""parse the output of go mod graph"""
import json
import networkx as nx
import os
import subprocess
from sbom2dot.dotgenerator import DOTGenerator
from lib4sbom.parser import SBOMParser
from lib4sbom.output import SBOMOutput
import pygraphviz
from networkx.drawing import nx_agraph
import matplotlib.pyplot as plt
import pandas as pd


def generate_go_sbom(target_dir: str, output_loc: str):
    """Currently uses: https://github.com/opensbom-generator/spdx-sbom-generator

    Args:
        target_dir (str): Base directory of target GO package
        output_loc (str): Output location for generated SBOM
    """
    # https://github.com/CycloneDX/cyclonedx-gomod
    # print("cyclonedx-gomod mod -json=true -output sbom.json")

    # make the output directory for SPDX-SBOM-Generator if it does not exist
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)

    # set the binary location of the tool, messy but fine for PoC
    spdx_binary_loc = "/home/td/Documents/SBOM/spdx-sbom-generator"

    # generate the command
    sbom_cmd = [f"(cd {target_dir} && {spdx_binary_loc} -o {output_loc})"]

    # run the command
    subprocess.run(sbom_cmd, shell=True, check=True)


def convert_sbom2graph(sbom_path: str):
    """Converts an SBOM to a graph.
    Relies on sbom2dot: https://github.com/anthonyharrison/sbom2dot

    Args:
        sbom_path (str): _description_
    """

    # parse the SBOM 
    dot_parser = SBOMParser()

    # parse the SBOM file
    dot_parser.parse_file(sbom_path)

    sbom_dot = DOTGenerator(dot_parser.get_sbom()["packages"])
    sbom_dot.generatedot(dot_parser.get_sbom()["relationships"])
    dot = sbom_dot.getDOT()
    
    # convert to a dot string
    dot_string = '\n'.join(dot)

    # generates a graph from the dot_string
    G = nx_agraph.from_agraph(pygraphviz.AGraph(dot_string))

    return G



def dependency_paths(temp_graph, source_node: str, target_node: str):
    """Prints all paths from a source node to a target node

    Args:
        temp_graph
        source_node (str): Source Node
        target_node (str): Target Node
    """
    """"""
    dotFormat = """
        digraph G {
        0 -> 1;
        1 -> 2;
        1 -> 3;
        2 -> 4;
        3 -> 4;
        4 -> 5;
        3 -> 6;
        }
    """

    for path in nx.all_simple_paths(temp_graph, 
                                    source=source_node, 
                                    target=target_node):
        print(path)

    # sorted(nx.ancestors(G, 'github.com/hashicorp/consul'))
    # print("use networkx to parse the graph")
    

