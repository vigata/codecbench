'''
Created on Jun 11, 2014

@author: alberto
'''

import subprocess
import os
import re

def libvpx_handler(run):
    """ does a run. returns metric info 
    returns:
    size of the encoded bitstream
    metric info SSIM/PSNR
    
    produces reconstructed yuv. provides size info 
    """
    
    root = os.path.dirname( __file__ ) + os.sep + run['platform'] + os.sep
    
    pars = {'codec': run['config'].get('libvpx_codec', "vp9"),
            'width': run['seq']['width'],
            'height': run['seq']['height'],
            'num' : run['seq']['fpsnum'],
            'den' : run['seq']['fpsden'],
            'bitrate' : run['config']['bitrate'],
            'output' : run['output'] +".webm",
            'cpu' : run['config'].get('cpu', 16),
            'input' : run['seq']['abspath'],
            'encoder' : os.path.abspath(root + "vpxenc"),
            'decoder' : os.path.abspath(root + "vpxdec"),
            'reconfile' : run['recon'],
            'vm' : run['tools']['vm'],
            'frame_count' : run['frame_count']
    }
    
    
    
    try:
        
        clines = []
        command = "{encoder} -v --cpu-used={cpu}  -p 1  --fps={num}/{den} --target-bitrate={bitrate} --codec={codec} -w {width} -h {height} -o {output} --limit={frame_count} {input}".format(**pars).split()
        # do encode
        out = subprocess.check_output(command,stderr=subprocess.STDOUT).decode("utf-8")
        
        #sample last line
        #Pass 1/1 frame  300/300   136845B    3649b/f  109476b/s   23550 ms (12.74 fps)[K
        search = re.compile("(\d+)B\s+(\d+)b/f\s+(\d+)b/s", re.MULTILINE ).search(out)
        (totalbytes, bitsperframe, bps) = search.groups()

        
        
        #do decode
        command = "{decoder}  {output} --i420  -o {reconfile}".format(**pars).split();
        out = subprocess.check_output(command)
        
        #retrieve metrics
        command = "{vm} -a {input} -b {reconfile} -m psnr,ssim -w {width} -h {height} -v -x {frame_count}".format(**pars).split()
        mout = subprocess.check_output(command).decode('utf-8')
        
        psnr = re.compile("psnr: (.+)$", re.MULTILINE ).search(mout).group(1) 
        ssim = re.compile("ssim: (.+)$", re.MULTILINE ).search(mout).group(1) 
        
        #delete recon if needed
        os.remove(run['recon']) if not run['keeprecon'] else None
        
        #print("psnr: {0}    ssim: {1}".format(psnr,ssim))
        run['results'] = {'psnr':float(psnr), 'ssim':float(ssim), 'totalbytes': int(totalbytes), 'bitsperframe': int(bitsperframe), 'bps':int(bps) }
        
        
            
        
    except subprocess.CalledProcessError as e:
        print (e.output)
        pass
    
    
codec = {
    "nickname": "libvpx",
    "profile": "libvpx",
    "out_extension": "webm",
    "handler" : libvpx_handler,
    "supported_pars" : {"bitrate":1000,"cpu":16,'libvpx_codec':'vp9'},
    "ratesweep_pars" : ['bitrate']
}


def init(gconf):
    """ returns codec struct """
    # figure out versions
    exe = os.path.dirname( __file__ ) + os.sep + gconf['platform'] + os.sep + 'vpxenc'
    try:
         
        p = subprocess.Popen( [exe], stderr=subprocess.PIPE, stdout=subprocess.PIPE )
        out, err = p.communicate()
        
        search = re.compile("vp8.+(v\d+\..*)", re.MULTILINE).search(err.decode())
        vp8ver, = search.groups()
        
        search = re.compile("vp9.+(v\d+\..*)", re.MULTILINE).search(err.decode())
        vp9ver, = search.groups()
        
        version = "vp8: {0}, vp9: {1}".format(vp8ver, vp9ver)
        version_long = version
    except:
        version = "?"
        version_long = "??"
        
    codec['version'] = version
    codec['version_long'] = version_long
    
    return codec
    

    