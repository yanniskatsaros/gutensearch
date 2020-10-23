import os
import sys
import logging

from argparse import ArgumentParser

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='[%(levelname)10s] %(asctime)s %(name)s - %(message)s'
)

def make_parser():
    ...