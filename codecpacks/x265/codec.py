'''
Created on Jun 11, 2014

@author: alberto
'''

import subprocess
import os
import re

def x265_handler(run):
    """ does a run. returns metric info 
    returns:
    size of the encoded bitstream
    metric info SSIM/PSNR
    
    produces reconstructed yuv. provides size info 
    """
    
    root = os.path.dirname( __file__ ) + os.sep + run['platform'] + os.sep
    
    pars = {'codec':"x265",
            'width': run['seq']['width'],
            'height': run['seq']['height'],
            'num' : run['seq']['fpsnum'],
            'den' : run['seq']['fpsden'],
            'bitrate' : run['config']['bitrate'],
            'preset' : run['config']['preset'] if 'preset' in run['config'] else 'slow',
            'muxedoutput' : run['output'] +".mp4",
            'output' : run['output']+".265",
            'input' : run['seq']['abspath'],
            'encoder' : os.path.abspath(root + "x265"),
            'decoder' : run['tools']['h265refdec'],
            'muxer' : run['tools']['mp4box'],
            'reconfile' : run['recon'],
            'vm' : run['tools']['vm'],
            'frame_count' : run['frame_count'],
            'platform' : run['platform']
    }
    
    
    
    try:
        
        clines = []
        
        command = "{encoder} --fps={num}/{den} --bitrate={bitrate} --input-res {width}x{height} --preset {preset} -o {output} --frames {frame_count} {input}".format(**pars).split()
        clines.append(command)
        # do encode
        out = subprocess.check_output(command,stderr=subprocess.STDOUT).decode("utf-8")
        
        #filesize
        filesize = os.path.getsize(pars['output'])
        
        #create muxed output for convenience
        command = "{muxer} -add {output} {muxedoutput}".format(**pars).split()
        out = subprocess.check_output(command,stderr=subprocess.STDOUT).decode("utf-8")
        
        framecount = run['seq']['frame_count']
        fps = pars['num']/pars['den']
        (totalbytes, bitsperframe, bps) = (filesize, filesize/framecount, (filesize*8)/(framecount/fps) )
        
        
        #do decode
        command = "{decoder}  -b {output}  -o {reconfile}".format(**pars).split();
        clines.append(command)
        out = subprocess.check_output(command)
        
        #retrieve metrics
        command = "{vm} -a {input} -b {reconfile} -m psnr,ssim -w {width} -h {height} -v -x {frame_count}".format(**pars).split()
        clines.append(command)
        mout = subprocess.check_output(command).decode('utf-8')
        
        psnr = re.compile("psnr: (.+)$", re.MULTILINE ).search(mout).group(1) 
        ssim = re.compile("ssim: (.+)$", re.MULTILINE ).search(mout).group(1) 
        
        #delete recon if needed
        os.remove(run['recon']) if not run['keeprecon'] else None
        
        #print("psnr: {0}    ssim: {1}".format(psnr,ssim))
        run['results'] = {'psnr':float(psnr), 'ssim':float(ssim), 'totalbytes': int(totalbytes), 'bitsperframe': int(bitsperframe), 'bps':int(bps), 'clines': clines }
        
        
            
        
    except subprocess.CalledProcessError:
        pass
    
    
codec = {
    "nickname": "x265",
    "profile": "x265",
    "out_extension": "mkv",
    "handler" : x265_handler,
    "supported_pars" : {"bitrate":1000,"preset":"fast"},
    "ratesweep_pars" : ['bitrate']
}

    
