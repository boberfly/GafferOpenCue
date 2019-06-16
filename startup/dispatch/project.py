import IECore
import Gaffer

dispatchers = []
import GafferOpenCue
dispatchers.append( GafferOpenCue.OpenCueDispatcher )

for dispatcher in dispatchers:
    Gaffer.Metadata.registerPlugValue( dispatcher, "jobName", "userDefault", "${script:name}" )
    directoryName = dispatcher.staticTypeName().rpartition( ":" )[2].replace( "Dispatcher", "" ).lower()
    Gaffer.Metadata.registerPlugValue( dispatcher, "jobsDirectory", "userDefault", "${project:rootDirectory}/dispatcher/" + directoryName )
