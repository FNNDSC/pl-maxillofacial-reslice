
#!/usr/bin/env python
"""
Developed by Arman Avesta, MD, PhD
FNNDSC | Boston Children's Hospital | Harvard Medical School
"""
# --------------------------------------------- ENVIRONMENT SETUP -----------------------------------------------------
# Project imports:
from reslicing_tools import axial_reslice

# System imports:
from chris_plugin import chris_plugin, PathMapper
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter

# Version:
__version__ = '1.0.0'

# ---------------------------------------------- ARGUMENT PARSING -----------------------------------------------------

DISPLAY_TITLE = r"""
pl-maxillofacial-reslice
"""

parser = ArgumentParser(description='This plugin takes in axial maxillofacial CTs '
                                    'and reslices them into coronal and sagittal images.',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')


# ------------------------------------------- ChRIS PLUGIN WRAPPER ----------------------------------------------------

# The main function of this *ChRIS* plugin is denoted by this ``@chris_plugin`` "decorator."
# Some metadata about the plugin is specified here. There is more metadata specified in setup.py.
#
# documentation: https://fnndsc.github.io/chris_plugin/chris_plugin.html#chris_plugin
@chris_plugin(
    parser=parser,
    title='pl-maxillofacial-reslice',
    category='PACS-integrated reslicing of 3D images',                 # ref. https://chrisstore.co/plugins
    min_memory_limit='100Mi',    # supported units: Mi, Gi
    min_cpu_limit='1000m',       # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit=0              # set min_gpu_limit=1 to enable GPU
)

# ----------------------------------------------- MAIN FUNCTION -------------------------------------------------------

def main(options: Namespace, inputdir: Path, outputdir: Path):
    """
    *ChRIS* plugins usually have two positional arguments: an **input directory** containing
    input files and an **output directory** where to write output files. Command-line arguments
    are passed to this main method implicitly when ``main()`` is called below without parameters.

    :param options: non-positional arguments parsed by the parser given to @chris_plugin
    :param inputdir: directory containing (read-only) input files
    :param outputdir: directory where to write output files
    """

    print(DISPLAY_TITLE)

    axial_dicoms_dir = inputdir / 'axial'
    coronal_dicoms_dir = outputdir / 'coronal'
    sagittal_dicoms_dir = outputdir / 'sagittal'

    axial_reslice(axial_dicoms_dir, coronal_dicoms_dir, sagittal_dicoms_dir)

# ------------------------------------------------ EXECUTE MAIN -------------------------------------------------------

if __name__ == '__main__':
    main()
