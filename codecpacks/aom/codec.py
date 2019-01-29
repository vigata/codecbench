'''
Created on Jan 29, 2019

@author: alberto
'''

import subprocess
import os
import re
import time

def aom_handler(run):
    """ does a run. returns metric info 
    returns:
    size of the encoded bitstream
    metric info SSIM/PSNR
    
    produces reconstructed yuv. provides size info 
    """
    
    root = os.path.dirname( __file__ ) + os.sep + run['platform'] + os.sep
    
    pars = {'codec': run['config'].get('aom_codec', "av1"),
            'width': run['seq']['width'],
            'height': run['seq']['height'],
            'num' : run['seq']['fpsnum'],
            'den' : run['seq']['fpsden'],
            'bitrate' : run['config']['bitrate'],
            'output' : run['output'] +".aom",
            'cpu' : run['config'].get('cpu', 8),
            'input' : run['seq']['abspath'],
            'encoder' : os.path.abspath(root + "aomenc"),
            'decoder' : os.path.abspath(root + "aomdec"),
            'reconfile' : run['recon'],
            'vm' : run['tools']['vm'],
            'frame_count' : run['frame_count']
    }
    
    
    
    try:
        
        clines = []
        command = "{encoder} -v --cpu-used={cpu}  -p 1  --fps={num}/{den} --target-bitrate={bitrate} --codec={codec} -w {width} -h {height} -o {output} --limit={frame_count} {input}".format(**pars).split()
        clines.append(command)
        # do encode
        startenc = time.time()
        out = subprocess.check_output(command,stderr=subprocess.STDOUT).decode("utf-8")
        stopenc = time.time()
        
        #sample last line
        #Pass 1/1 frame  300/300   136845B    3649b/f  109476b/s   23550 ms (12.74 fps)[K
        search = re.compile("(\d+)B\s+(\d+)b/f\s+(\d+)b/s", re.MULTILINE ).search(out)
        (totalbytes, bitsperframe, bps) = search.groups()

        
        
        #do decode
        command = "{decoder}  {output} --i420  -o {reconfile}".format(**pars).split();
        clines.append(command)
        out = subprocess.check_output(command)
        
        run['results'] = {'totalbytes': int(totalbytes), 'bitsperframe': int(bitsperframe), 'bps':int(bps), 'encodetime_in_s': (stopenc-startenc), 'clines': clines}
        
        
        #do video metrics
        metrics = run['tools']['do_video_metrics'](clines, **pars)
        run['results'].update(metrics)
        
        #delete recon if needed
        os.remove(run['recon']) if not run['keeprecon'] else None
        
        
    except subprocess.CalledProcessError as e:
        print (e.output)
        pass
    
    
codec = {
    "nickname": "aom",
    "profile": "aom",
    "out_extension": "aom",
    "handler" : aom_handler,
    "supported_pars" : {"bitrate":1000,"cpu":8,'aom_codec':'av1'},
    "ratesweep_pars" : ['bitrate']
}


def init(gconf):
    """ returns codec struct """
    # figure out versions
    exe = os.path.dirname( __file__ ) + os.sep + gconf['platform'] + os.sep + 'aomenc'
    try:
         
        p = subprocess.Popen( [exe, "--help"], stderr=subprocess.PIPE, stdout=subprocess.PIPE )
        out, err = p.communicate()
        out = out.decode().replace('\r\n','\n')
        
        search = re.compile("av1.+?-(.*)$", re.MULTILINE).search(out)
        av1ver,  = search.groups()
        
        version = "av1: {0}".format(av1ver)
        version_long = version
    except Exception as e:
        version = "?"
        version_long = "??"
        
    codec['version'] = version
    codec['version_long'] = version_long
    
    return codec
    

    
