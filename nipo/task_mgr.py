#Note: Contrary to the name of the module, this files only contains
#Config for the task manager. Actual definition of tasks is handled
#by a decorator around the task functions

from celery import Celery

def get_celery_app():	
	celery_app = Celery('nipo',
						broker='redis://',
						backend='redis://',
						include=['nipo.nipo_api'])

	celery_app.conf.update(
		result_expires=3600
		)

	return celery_app

#if __name__ == '__main__':
# 	celery_app.start()