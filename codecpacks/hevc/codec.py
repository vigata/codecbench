'''
Created on Jun 11, 2014

@author: alberto
'''

import subprocess
import os
import re

def hevchm_handler(run):
    """ does a run. returns metric info 
    returns:
    size of the encoded bitstream
    metric info SSIM/PSNR
    
    produces reconstructed yuv. provides size info 
    """
    
    root = os.path.dirname( __file__ ) + os.sep + run['platform'] + os.sep
    
    pars = {'platform' : run['platform'], 
            'root' : root,
            'codec':"hevchm",
            'width': run['seq']['width'],
            'height': run['seq']['height'],
            'num' : run['seq']['fpsnum'],
            'den' : run['seq']['fpsden'],
            'bitrate' : run['config']['bitrate']*1000,
            'muxedoutput' : run['output'] +".mp4",
            'output' : run['output']+".hevc",
            'input' : run['seq']['abspath'],
            'encoder' : os.path.abspath(root + "TAppEncoder"),
            'decoder' : os.path.abspath(root + "TAppDecoder"),
            'muxer' : os.path.abspath(root + "MP4Box"),
            'reconfile' : run['recon'],
            'vm' : run['tools']['vm'],
            'frame_count' : run['frame_count'],
            'preset' : run['config']['preset'] if 'preset' in run['config'] else 'default'
    }
    
    
    
    try:
        
        clines = []
        
        command = "{encoder} -c {root}{preset}.cfg -fr {num}/{den} -f {frame_count} --TargetBitrate={bitrate} --SourceWidth={width} --SourceHeight={height} -b {output} -i {input} --ReconFile={reconfile}".format(**pars)
        clines.append(command)
        # do encode
        out = subprocess.check_output(command.split(),stderr=subprocess.STDOUT).decode("utf-8")
        
        #sample last line
        #Pass 1/1 frame  300/300   136845B    3649b/f  109476b/s   23550 ms (12.74 fps)[K
        filesize = os.path.getsize(pars['output'])
        
        #create muxed output for convenience
        command = "{muxer} -add {output} {muxedoutput}".format(**pars).split()
        out = subprocess.check_output(command,stderr=subprocess.STDOUT).decode("utf-8")
        
        framecount = pars['frame_count']
        fps = pars['num']/pars['den']
        (totalbytes, bitsperframe, bps) = (filesize, filesize/framecount, (filesize*8)/(framecount/fps) )
        
        
        # no need to do decode. we get recon from encoder
        #command = "{decoder}  -p InputFile={output}  -p OutputFile={reconfile}".format(**pars).split();
        #clines.append(command)
        #out = subprocess.check_output(command)
        
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
        
        
            
        
    except subprocess.CalledProcessError as e:
        print(command)
        print(e)
        print(e.output)
        pass
    
    
codec = {
    "nickname": "hevchm",
    "profile": "hevchm",
    "out_extension": "mp4",
    "handler" : hevchm_handler,
    "supported_pars" : {"bitrate":1000,'preset':"default"},
    "ratesweep_pars" : ['bitrate']
}

def init(gconf):
    """ returns codec struct """
    # figure out versions
    exe = os.path.dirname( __file__ ) + os.sep + gconf['platform'] + os.sep + 'TAppEncoder'
    try:
         
        p = subprocess.Popen( [exe], stderr=subprocess.PIPE, stdout=subprocess.PIPE )
        out, err = p.communicate()
        
        search = re.compile("^(HM.+)$", re.MULTILINE).search(out.decode())
        ver, = search.groups()
        
        
        version = ver 
        version_long = version
    except:
        version = "?"
        version_long = "??"
        
    codec['version'] = version
    codec['version_long'] = version_long
    
    return codec
    
    
