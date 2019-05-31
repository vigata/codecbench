'''
Created on Jun 11, 2014

@author: alberto
'''

import subprocess
import os
import re
import time
import random


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
            'intres' : run['config']['intres'] if 'intres' in run['config'] else "",
            'muxedoutput' : run['output'] +".mp4",
            'output' : run['output']+".264",
            'input' : run['seq']['abspath'],
            'encoder' : os.path.abspath(root + "x264"),
            'decoder' : os.path.abspath(root + "ldecod"),
            'reconfile' : run['recon'],
            'vm' : run['tools']['vm'],
            'vgtmpeg' : run['tools']['vgtmpeg'],
            'ffmpeg'  : run['tools']['ffmpeg'],
            'muxer' : run['tools']['mp4box'],
            'frame_count' : run['frame_count'],
            'platform' : run['platform'],
            'metrics' : run['metrics'] if 'metrics' in run else ['psnr']
    }
    
    
    
    try:
        
        clines = []

        #if intres, internal resolution is specified, coding happens at this resolution. yet metric comparison is at original resolution
        intres = None
        intres_codec_input = ""
        intres_codec_output = ""
        if pars['intres']!='':
            intres = pars['intres'].split('x')
            pars['in_w'] = pars['width']
            pars['in_h'] = pars['height']
            pars['out_w'] = intres[0]
            pars['out_h'] = intres[1]
            intres_codec_yuv_input = "tmp/"+str(random.getrandbits(128))+'.yuv'
            intres_codec_yuv_output= "tmp/"+str(random.getrandbits(128))+'.yuv'



        #if intres create temp version of input at w x h of int res
        if intres:
            run['tools']['do_yuv_resize'](run, pars['input'], intres_codec_yuv_input ,clines, **pars)


        encoder_yuv_input = pars['input'] if not intres  else os.path.abspath(intres_codec_yuv_input)
        encode_width = pars['width']     if not intres  else pars['out_w']
        encode_height= pars['height']    if not intres  else pars['out_h']

        command = "{encoder} -v --fps={num}/{den} --bitrate={bitrate} --input-res {2}x{3} --preset {preset} -o {1} --frames {frame_count} {0}".format(encoder_yuv_input, pars['output'], encode_width, encode_height, **pars).split()
        clines.append(command)
        # do encode
        startenc = time.time()
        out = subprocess.check_output(command,stderr=subprocess.STDOUT).decode("utf-8")
        stopenc = time.time()

        # delete tmp file if using intres
        if intres!=None:
            os.remove(encoder_yuv_input)

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
            # this path uses ffmpeg to do the h264 decode and upsampling if necessary
            if not intres:
                command = "{vgtmpeg}  -i {output} -y -map 0 -pix_fmt yuv420p -vsync 0 {reconfile}".format(**pars).split();
            else:
                command = "{ffmpeg}  -i {output} -y  -vf scale={width}:{height} -pix_fmt yuv420p -vsync 0 {reconfile}".format(**pars).split();

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
    "supported_pars" : {"bitrate":1000,"preset":"fast", "intres":"", "metrics":"psnr"},
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
