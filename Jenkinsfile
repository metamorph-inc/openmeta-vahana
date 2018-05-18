pipeline {
  agent any
  stages {
    stage('OpenMETA runner') {
      parallel {
        stage('OpenMETA runner') {
          steps {
            openMetaTestBench(modelName: 'openmeta-vahana.xme')
          }
        }
        stage('OpenMETA Runner 2') {
          steps {
            openMetaTestBench(modelName: 'openmeta-vahana.xme')
          }
        }
      }
    }
  }
}