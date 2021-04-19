#Note: Contrary to the name of the module, this files only contains
#Config for the task manager. Actual definition of tasks is handled
#by a decorator around the task functions

from celery import Celery

celery_app = Celery('nipo',
					broker='pyamqp://guest@localhost//',
					backend='rpc://',
					include=['nipo.nipo_api'])

celery_app.conf.update(
	result_expires=3600
	)

#if __name__ == '__main__':
# 	celery_app.start()