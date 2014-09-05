'''
Created on Jun 11, 2014

@author: alberto
'''

import subprocess
import os
import re
import time


def x264_handler(run):
    """ does a run. returns metric info 
    returns:
    size of the encoded bitstream
    metric info SSIM/PSNR
    
    produces reconstructed yuv. provides size info 
    """

    root = os.path.dirname( __file__ ) + os.sep + run['platform'] + os.sep
    
    pars = {'codec':"x264",
            'width': run['seq']['width'],
            'height': run['seq']['height'],
            'num' : run['seq']['fpsnum'],
            'den' : run['seq']['fpsden'],
            'bitrate' : run['config']['bitrate'],
            'preset' : run['config']['preset'] if 'preset' in run['config'] else 'slow',
            'muxedoutput' : run['output'] +".mp4",
            'output' : run['output']+".264",
            'input' : run['seq']['abspath'],
            'encoder' : os.path.abspath(root + "x264"),
            'decoder' : os.path.abspath(root + "ldecod"),
            'reconfile' : run['recon'],
            'vm' : run['tools']['vm'],
            'vgtmpeg' : run['tools']['vgtmpeg'],
            'muxer' : run['tools']['mp4box'],
            'frame_count' : run['frame_count'],
            'platform' : run['platform']
    }
    
    
    
    try:
        
        clines = []
        
        command = "{encoder} -v --fps={num}/{den} --bitrate={bitrate} --input-res {width}x{height} --preset {preset} -o {output} --frames {frame_count} {input}".format(**pars).split()
        clines.append(command)
        # do encode
        startenc = time.time()
        out = subprocess.check_output(command,stderr=subprocess.STDOUT).decode("utf-8")
        stopenc = time.time()
        
        #sample last line
        #Pass 1/1 frame  300/300   136845B    3649b/f  109476b/s   23550 ms (12.74 fps)[K
        search = re.compile("(\d+)B\s+(\d+)b/f\s+(\d+)b/s", re.MULTILINE ).search(out)
        filesize = os.path.getsize(pars['output'])
        
        #create muxed output for convenience
        command = "{muxer} -add {output} {muxedoutput}".format(**pars).split()
        out = subprocess.check_output(command,stderr=subprocess.STDOUT).decode("utf-8")
        
        framecount = run['seq']['frame_count']
        fps = pars['num']/pars['den']
        (totalbytes, bitsperframe, bps) = (filesize, filesize/framecount, (filesize*8)/(framecount/fps) )
        
        
        #do decode.
        if True:
            command = "{vgtmpeg}  -i {output} -y -map 0 -pix_fmt yuv420p -vsync 0 {reconfile}".format(**pars).split();
            clines.append(command)
            out = subprocess.check_output(command, stderr=subprocess.STDOUT)
        else:
            #do decode
            command = "{decoder}  -p InputFile={output}  -p OutputFile={reconfile}".format(**pars).split();
            clines.append(command)
            out = subprocess.check_output(command)
        
        run['results'] = {'totalbytes': int(totalbytes), 'bitsperframe': int(bitsperframe), 'bps':int(bps), 'encodetime_in_s': (stopenc-startenc), 'clines': clines}
        
        #do video metrics
        metrics = run['tools']['do_video_metrics'](clines, **pars)
        run['results'].update(metrics)
        
        #delete recon if needed
        os.remove(run['recon']) if not run['keeprecon'] else None
        
    except subprocess.CalledProcessError as e:
        pass
    
        
    
    
codec = {
    "nickname": "x264",
    "profile": "x264",
    "out_extension": "mkv",
    "handler" : x264_handler,
    "version" : "",
    "version_long" : "",
    "supported_pars" : {"bitrate":1000,"preset":"fast"},
    "ratesweep_pars" : ['bitrate']
}

    
def init(gconf):
    """ returns codec struct """
    # figure out versions
    exe = os.path.dirname( __file__ ) + os.sep + gconf['platform'] + os.sep + 'x264'
    try:
        out = subprocess.check_output([exe , "--version"], stderr=subprocess.STDOUT)
        version =  out.splitlines()[0].decode()
        version_long = out.decode()
    except:
        version = "?"
        version_long = "??"
        
    codec['version'] = version
    codec['version_long'] = version_long
    
    return codec
