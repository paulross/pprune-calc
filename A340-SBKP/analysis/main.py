"""
Call the plot and markdown generation code.

pprune forum: https://www.pprune.org/rumours-news/613321-air-x-340-brasil.html
14th Sep 2018, 03:13

"""
import sys

from analysis import plot
from analysis import readme


def main():
    return plot.main() or readme.main()


if __name__ == '__main__':
    sys.exit(main())
