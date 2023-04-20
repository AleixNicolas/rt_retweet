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

    path= infile.name.split('/')[-1].split('.')[-2]
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)
        
    
    path= path+'/I-'+str(interval)+'_g-'+str(granularity)+'_d-'+str(decay)+'_t-'+str(threshold)
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)
       
    if outfile is None:
            outfile = str(path+'/'+infile.name.split('/')[-1].split('.')[-2])+'_elites.csv'
        
    if elites:
        el.main(infile, decay, threshold, granularity, interval, outfile)
        
    path= path+'/a-'+str(alpha)+'_m-'+method+'_l-'+algorithm
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)
        
    if dendrogram:
        de.main(infile, outfile, decay, threshold, granularity, interval, alpha, method, algorithm, path)
        
    logging.info('Finished.')  
    
main()