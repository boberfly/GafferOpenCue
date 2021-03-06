##########################################################################
#
#  Copyright (c) 2019, Alex Fuller. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of Alex Fuller nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os

from outline import Outline, cuerun
from outline.modules.shell import Shell

import IECore

import Gaffer
import GafferDispatch

class OpenCueDispatcher( GafferDispatch.Dispatcher ) :

	def __init__( self, name = "OpenCueDispatcher" ) :

		GafferDispatch.Dispatcher.__init__( self, name )

		self["service"] = Gaffer.StringPlug( defaultValue = 'default' )
		self["envKey"] = Gaffer.StringPlug()
		self["showName"] = Gaffer.StringPlug( defaultValue = "${project:showName}" )
		self["shotName"] = Gaffer.StringPlug( defaultValue = "${project:shotName}" )
		self["userName"] = Gaffer.StringPlug( defaultValue = os.environ.get('USER') )

	## Emitted prior to spooling the OpenCue job, to allow
	# custom modifications to be applied.
	@classmethod
	def preSpoolSignal( cls ) :

		return cls.__preSpoolSignal

	__preSpoolSignal = Gaffer.Signal2()

	def _doDispatch( self, rootBatch ) :

		# Construct an object to track everything we need
		# to generate the job. I have a suspicion that at
		# some point we'll want a Dispatcher::Job base class
		# which _doDispatch() must return, in which case this
		# might just be member data for a subclass of one of those.
		dispatchData = {}
		dispatchData["scriptNode"] = rootBatch.preTasks()[0].node().scriptNode()
		dispatchData["scriptFile"] = Gaffer.Context.current()["dispatcher:scriptFileName"]
		dispatchData["batchesToLayers"] = {}

		# Create an OpenCue outline and set its basic properties.

		context = Gaffer.Context.current()

		outline = Outline( 
			context.substitute( self["jobName"].getValue() ) or "untitled",
			show = context.substitute( self["showName"].getValue() ) or "show",
			shot = context.substitute( self["shotName"].getValue() ) or "shot",
			user = context.substitute( self["userName"].getValue() ) or "user",
		)

		# Populate the job with tasks from the batch tree
		# that was prepared by our base class.

		for upstreamBatch in rootBatch.preTasks() :
			self.__buildOutlineWalk( outline, upstreamBatch, dispatchData )

		# Signal anyone who might want to make just-in-time
		# modifications to the job.

		self.preSpoolSignal()( self, outline )

		# Finally, we can spool the job.

		cuerun.launch( outline, use_pycuerun = False )


	def __buildOutlineWalk( self, opencueOutline, batch, dispatchData ) :

		layer = self.__acquireLayer( batch, dispatchData )
		opencueOutline.add_layer( layer )

		if batch.blindData().get( "opencueDispatcher:visited" ) :
			return

		for upstreamBatch in batch.preTasks() :
			upstreamLayer = self.__buildOutlineWalk( opencueOutline, upstreamBatch, dispatchData )
			layer.depend_on( upstreamLayer )

		batch.blindData()["opencueDispatcher:visited"] = IECore.BoolData( True )

	def __acquireLayer( self, batch, dispatchData ) :

		layer = dispatchData["batchesToLayers"].get( batch )
		if layer is not None :
			return layer

		# Make a layer.

		nodeName = batch.node().relativeName( dispatchData["scriptNode"] )
		layerName = nodeName

		# Generate a `gaffer execute` command line suitable for
		# executing all the frames in the batch.

		args = [
			"gaffer", "execute",
			"-script", dispatchData["scriptFile"],
			"-nodes", nodeName,
		]

		frames = None

		if batch.frames() :
			frames = str( IECore.frameListFromList( [ int( x ) for x in batch.frames() ] ) )
			args.extend( [ "-frames", frames ] )
			layerName += "_" + frames

		scriptContext = dispatchData["scriptNode"].context()
		contextArgs = []
		for entry in [ k for k in batch.context().keys() if k != "frame" and not k.startswith( "ui:" ) ] :
			if entry not in scriptContext.keys() or batch.context()[entry] != scriptContext[entry] :
				contextArgs.extend( [ "-" + entry, IECore.repr( batch.context()[entry] ) ] )

		if contextArgs :
			args.extend( [ "-context" ] + contextArgs )

		# Apply any custom dispatch settings to the command.

		service = None

		layerArgs = {
			"command" : args,
			"chunk" : batch.node()["dispatcher"]["batchSize"].getValue(),
			"range" : frames,
			"threads" : None,
			"threadable" : None,
			"memory" : None,
			"tags" : None,
		}

		opencuePlug = batch.node()["dispatcher"].getChild( "opencue" )

		if opencuePlug is not None :
			threadable = opencuePlug["threadable"].getValue()
			threads = opencuePlug["threads"].getValue()
			layerArgs["threadable"] = threadable
			if not threadable :
				layerArgs["threads"] = 1
			elif threads > 0 :
				layerArgs["threads"] = threads
			memory = opencuePlug["memory"].getValue()
			if memory > 0 :
				layerArgs["memory"] = memory
			tags = opencuePlug["tags"].getValue()
			if tags:
				layerArgs["tags"] = tags
			service = opencuePlug["service"].getValue()
		
		# Create an OpenCue Shell to execute that command line, which is a subclassed layer

		layer = Shell(  layerName, 
						command = layerArgs['command'],
						chunk = layerArgs['chunk'],
						range = layerArgs['range'],
						threads = layerArgs['threads'],
						threadable = layerArgs['threadable'],
						memory = layerArgs['memory'],
						tags = layerArgs['tags'],
		)

		layer.set_service( service )

		# Remember the task for next time, and return it.

		dispatchData["batchesToLayers"][batch] = layer
		return layer

	@staticmethod
	def _setupPlugs( parentPlug ) :

		if "opencue" in parentPlug :
			return

		parentPlug["opencue"] = Gaffer.Plug()
		parentPlug["opencue"]["threads"] = Gaffer.IntPlug()
		parentPlug["opencue"]["threadable"] = Gaffer.BoolPlug( defaultValue = True )
		parentPlug["opencue"]["memory"] = Gaffer.IntPlug()
		parentPlug["opencue"]["tags"] = Gaffer.StringPlug()
		parentPlug["opencue"]["service"] = Gaffer.StringPlug( defaultValue = 'default' )

IECore.registerRunTimeTyped( OpenCueDispatcher, typeName = "GafferOpenCue::OpenCueDispatcher" )

GafferDispatch.Dispatcher.registerDispatcher( "OpenCue", OpenCueDispatcher, OpenCueDispatcher._setupPlugs )
