#!/usr/bin/python
import logging
import mesos.interface
from mesos.interface import mesos_pb2
import mesos.native
from appConfig import AppConfig
from taskStatus import TaskStatus

class MyMesosScheduler(mesos.interface.Scheduler):

  def __init__(self, implicitAcknowledgements, executor):
    self.implicitAcknowledgements = implicitAcknowledgements
    self.executor = executor
    self.status = TaskStatus()
    #configure logging
    self.logger = logging.getLogger('mesos_framework')
    formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    self.logger.addHandler(ch)
    self.app_list = []

  def registered(self, driver, frameworkId, masterInfo):
    self.logger.info("Registered with framework ID %s" % frameworkId.value)

  def addApp(self,appconfig):
    self.app_list.append(appconfig)

  def getTaskList(self):
    return self.status.getDict()

  def resourceOffers(self, driver, offers):
    '''
    Basic placement strategy (loop over offers and try to push as possible)
    '''
    id1 = 0
    offerCpus=0
    offerMem=0
    self.logger.info("just got an offer")
    for offer in offers:
      offer_tasks = []
      for resource in offer.resources:
        if resource.name == "cpus":
          offerCpus += resource.scalar.value
        elif resource.name == "mem":
          offerMem += resource.scalar.value
      print "Received offer %s with cpus: %s and mem: %s" \
                        % (offer.id.value, offerCpus, offerMem)
      if (not self.app_list):
        self.logger.info("declining offer since no apps to run")
        driver.declineOffer(offer.id)
        continue
      appconfig = self.app_list.pop()
      if (offerCpus>=appconfig.cpus and offerMem>=appconfig.ram):
        task = self.new_docker_task(offer, offer.id.value, appconfig)
        self.logger.info("testing logging after initializing task")
        offer_tasks.append(task)
        #id1 += 1
        driver.launchTasks(offer.id, offer_tasks)
        #we now add the tasks in taskStatus object
        self.status.addApp(appconfig.getName())
        self.status.addTask(offer.id.value, appconfig.getName())
      else:
        self.logger.info("resource offer was too low")
      self.logger.info("Finished ")	
      
    '''
    for offer in offers:
    self.logger.info(offer)
    # Let's decline the offer for the moment
    '''

  def statusUpdate(self, driver, update):
    '''
    when a task is over, killed or lost (slave crash, ....), this method
    will be triggered with a status message.
    '''
    self.logger.info("Task %s is in state %s" % \
    (update.task_id.value, mesos_pb2.TaskState.Name(update.state)))
    # we update the status of the app
    self.status.updateStatus(update.task_id.value, mesos_pb2.TaskState.Name(update.state))
    # we log the status for a sanity check
    self.logger.info("Statuses - %s", self.status.getDict())

  def frameworkMessage(self, driver, executorId, slaveId, message):
    self.logger.info("Received framework message")

  def new_docker_task(self, offer, id, appconfig):
    '''
    Creates a task for mesos

    :param offer: mesos offer
    :type offer: Offer
    :param id: Id of the task (unique)
    :type id: str
    :param appconfig: config of application to be launched
    :type appconfig: Appconfig
    '''

    task = mesos_pb2.TaskInfo()
    '''
    # We want of container of type Docker
    container = mesos_pb2.ContainerInfo()
    container.type = 1 # mesos_pb2.ContainerInfo.Type.DOCKER
    '''

    # Let's create a volume
    # container.volumes, in mesos.proto, is a repeated element
    # For repeated elements, we use the method "add()" that returns an object that can be updated
    '''
    if (appconfig.needStorage()):
      volume = container.volumes.add()
      #volume.container_path = appconfig.getStorage() # Path in container
      #TODO: we need to generate paths on host based on hash
      volume.host_path = "/tmp/mesosexample" # Path on host
      volume.mode = 1 # mesos_pb2.Volume.Mode.RW
      #volume.mode = 2 # mesos_pb2.Volume.Mode.RO
    '''
    # Define the command line to execute in the Docker container
    command = mesos_pb2.CommandInfo()
    command.value = appconfig.getCmd()
    task.command.MergeFrom(command) # The MergeFrom allows to create an object then to use this object in an other one. Here we use the new CommandInfo object and specify to use this instance for the parameter task.command.

    task.task_id.value = id
    task.slave_id.value = offer.slave_id.value
    task.name = appconfig.getName() 

    # CPUs are repeated elements too
    cpus = task.resources.add()
    cpus.name = "cpus"
    cpus.type = mesos_pb2.Value.SCALAR
    cpus.scalar.value = appconfig.getCpus() 

    # Memory are repeated elements too
    mem = task.resources.add()
    mem.name = "mem"
    mem.type = mesos_pb2.Value.SCALAR
    mem.scalar.value = appconfig.getRam() 

    '''
    # Let's focus on the Docker object now
    docker = mesos_pb2.ContainerInfo.DockerInfo()
    docker.image = appconfig.getImage() 
    docker.network = 2 # mesos_pb2.ContainerInfo.DockerInfo.Network.BRIDGE
    docker.force_pull_image = True
    '''

    '''
    #create parameter object to pass the weave information
    param = docker.parameters.add()
    param.key = "net"
    param.value = "weave"

    # Set docker info in container.docker
    container.docker.MergeFrom(docker)
    # Set docker container in task.container
    task.container.MergeFrom(container)
    '''

    # Return the object
    return task

def create():
    executor = mesos_pb2.ExecutorInfo()
    executor.executor_id.value = "mydocker"
    executor.name = "My docker example executor"
    implicitAcknowledgements = 1

    mesosScheduler = MyMesosScheduler(implicitAcknowledgements, executor)
    return mesosScheduler
if __name__ == "__main__":
  executor = mesos_pb2.ExecutorInfo()
  executor.executor_id.value = "mydocker"
  executor.name = "My docker example executor"
  
  framework = mesos_pb2.FrameworkInfo()
  framework.user = "" # Have Mesos fill in the current user.
  framework.name = "MyMesosDockerExample"

  implicitAcknowledgements = 1
  
  logging.basicConfig(level=logging.DEBUG)
  framework.principal = "docker-mesos-example-framework"
  mesosScheduler = MyMesosScheduler(implicitAcknowledgements, executor)
  # adding a custom application - this should be done by the REST API
  diction = {}
  diction["name"] = "test-app"
  diction["cpu"] = 1
  diction["ram"] = 1024
  diction["command"] = "echo hello mesos; sleep 10"
  #diction["docker_image"] = "centos"
  diction["storage"] = False
  app = AppConfig(diction)
  mesosScheduler.addApp(app)
  print mesosScheduler.app_list
  driver = mesos.native.MesosSchedulerDriver(
       mesosScheduler,
           framework,
           '127.0.0.1:5050') # I suppose here that mesos master url is local

  driver.run()

