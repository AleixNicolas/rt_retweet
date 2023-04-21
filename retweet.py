import click
import logging
import os
import elites as el
import dendrogram as de
from io import TextIOWrapper

logging.getLogger().setLevel(logging.INFO)

@click.command()
@click.option('--elites/--no-elites', required=False, default=True)
@click.option('--dendrogram/--no-dendrogram', required=False, default=False)
@click.option('-d', '--decay', type=click.FLOAT, required=False, default='1')
@click.option('-g', '--granularity', required=False, default=None, type=click.STRING)
@click.option('-t', '--threshold', required=False, default=None, type=click.FLOAT)
@click.option('-i', '--interval', required=False, type=click.STRING)
@click.option('-a', '--alpha', type=click.FLOAT, required=False, default='1')
@click.option('-m', '--method', type=click.STRING, default = 'ward')
@click.option('-l', '--algorithm', type=click.STRING, default = 'generic')
@click.option('-o', '--outfile', required=False, type=click.STRING, default=None)
@click.argument('infile', type=click.File('r'), default='-')
def main(infile: TextIOWrapper,
         elites: bool,
         dendrogram:bool,
         decay: float,
         threshold: float,
         granularity: str,
         interval: str,
         alpha: float,
         method: str,
         algorithm: str,
         outfile: str):
    
    # Exceptions
    if algorithm != 'nn_chain' and algorithm != 'generic':
        raise click.BadOptionUsage('algorithm', 'Non valid algorithm; algorithm must be nn_chain or generic; default is generic')
        
    if algorithm == 'generic' and method != 'centroid' and method != 'poldist' and method != 'ward':
        raise click.BadOptionUsage('method', 'Non valid method; for generic algorithm; method must be poldist, centroid or ward; default is ward')

    if algorithm == 'nn_chain' and method != 'ward':
        raise click.BadOptionUsage('method', 'Non valid method; for nn_chain algorithm; method must be ward; default is ward')
        
    if not 0<decay<=1:
        raise click.BadOptionUsage('method', 'Non valid value for decay; must be between 0 and 1')
        
    if not 0<alpha<1.6:
        raise click.BadOptionUsage('method', 'Non valid value for alpha; must be between 0 and 1.6')
        
    logging.info('Initializing')  
        
    #Create directory for dataset.
    path= infile.name.split('/')[-1].split('.')[-2]
    if not os.path.exists(path):
        os.makedirs(path)
        
    #Create subdirectory for elites.
    path= path+'/I-'+str(interval)+'_g-'+str(granularity)+'_d-'+str(decay)+'_t-'+str(threshold)
    if not os.path.exists(path):
        os.makedirs(path)
    
    #Generate name for elite file if none is given.
    if outfile is None:
            outfile = str(path+'/'+infile.name.split('/')[-1].split('.')[-2])+'_elites.csv'
    
    #Generate elite file if required.
    if elites:
        el.main(infile, decay, threshold, granularity, interval, outfile)

    #Create directory for graphs and generate dendrogram if required.
    if dendrogram:
        path= path+'/a-'+str(alpha)+'_m-'+method+'_l-'+algorithm
        if not os.path.exists(path):
            os.makedirs(path)
        de.main(infile, outfile, decay, threshold, granularity, interval, alpha, method, algorithm, path)
        
    logging.info('Finished.')
    
def get_file_info(file_wrapper: TextIOWrapper):
    # Get the file path
    file_path = file_wrapper.name
    # Get the directory path
    dir_path = os.path.dirname(file_path)
    # Get the base name (file name with extension)
    base_name = os.path.basename(file_path)
    # Split the file name and extension, then return the file name without extension
    file_name, _ = os.path.splitext(base_name)
    return file_name, dir_path
    
main()