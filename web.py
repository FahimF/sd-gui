import streamlit as st
from config import Config
from PIL import Image

class GenerateView:
	def __init__(self):
		# Load configuration info
		self.cfg = Config()
		self.files = []
		self.seeds = []
		self.file_index = -1
		st.set_page_config(layout="wide")

	def prompts_changed(self):
		print('Prompts changed')

	def show_previous(self):
		print('Show previous')

	def show_next(self):
		print('Show next')

	def delete_image(self):
		print('Delete image')


	def create_ui(self):
		# Main title
		st.title('Stable Diffusion')
		# Main tabs
		tab1, tab2, tab3 = st.tabs(["Generate", "Prompts", "Gallery"])
		# Generate tab
		with tab1:
			# Header
			st.header("Generate")
			self.prompt = st.text_area('Prompt', value=self.cfg.prompt.prompt, help='The text prompt used to generate a new image', placeholder='Please enter prompt')
			self.prompts = st.selectbox('', options=self.cfg.string_prompts(), index=0, help='Your last 20 prompts. Select a prompt from here to update the prompt input field', on_change=self.prompts_changed)
			# Image input
			with st.expander("Image input"):
				st.write("Add an image here only if you want to do img2img generation. Both your text prompt and the image will be used together.")
				img_col1, img_col2, = st.columns([4, 1])
				with img_col1:
					self.img_input = st.file_uploader('Choose image', type=['png', 'jpg', 'jpeg'], help='Input image for img2img generation')
				with img_col2:
					if self.img_input is not None:
						data = self.img_input.getvalue()
						st.image(data, width=128)
					# Noise strength
					self.noise = st.slider('Noise Strength', min_value=0.0, max_value=1.0, value=0.6, step=0.1, help='How much the input image affects the generated image')
					# Main interface two columns - settings & image
			col1, col2 = st.columns(2)
			with col1:
				# Scheduler
				schedulers = ['Default', 'LMS', 'PNDM', 'DDIM']
				sind = schedulers.index(self.cfg.scheduler)
				self.scheduler = st.selectbox('Scheduler', options=schedulers, index=sind, help='The scheduler/sampler to use for image generation')
				# Image size
				st.subheader('Image Size')
				st.write('Dimensions of generated image. Preferably, one side should be 512.')
				self.width = st.slider('Width', min_value=64, max_value=2048, value=self.cfg.width, step=8, help='The desired width of the output image')
				self.height = st.slider('Height', min_value=64, max_value=2048, value=self.cfg.height, step=8, help='The desired height of the output image')
				# Inference steps
				self.steps = st.slider('Number of Inference Steps', min_value=1, max_value=300, value=self.cfg.num_inference_steps, step=1, help='The number of inference steps. The more steps, the better the results, but longer it takes.')
				# Guidance
				self.guidance = st.slider('Guidance', min_value=-15.0, max_value=30.0, value=self.cfg.guidance_scale, step=0.1, help='How closely the final output adheres to the prompt. The lower the value, the less adherence to the prompt. Generally 0 to 15 or so but can go lower and higher.')
				# Number of images
				self.copies = st.number_input('Number of Images', min_value=1, max_value=20, value=self.cfg.num_copies, step=1, help='The number of images to generate in this batch.')
				# Seed
				self.seed = st.text_input('Seed', value=self.cfg.seed, help='The seed to use for image generation. Keep value at -1 for a random seed. If you specify a seed value, any image will be the same for that particular seed.')
			with col2:
				# Image
				if self.file_index > -1:
					path = self.files[self.file_index]
					pi = Image.open(path)
					st.image(pi, use_column_width='auto')
			# Info row
			flen = len(self.files)
			c, c1, c2, c3 = st.columns([4,1,2,1])
			with c:
				st.empty()
			with c1:
				st.empty()
			with c2:
				# Seed
				val = ''
				if flen > 0:
					s = self.seeds[self.file_index]
					val = f'{s}'
				st.text_input('Seed', value=val, disabled=True, help='The seed for current image. If you use this seed value, the same image will be generated again.')
			with c3:
				st.empty()
			# Actions and info row
			c, c1, c2, c3 = st.columns([3,1,1,1])
			with c:
				st.empty()
			with c1:
				# Previous
				state = self.file_index == 0 or flen == 0
				st.button('Previous', on_click=self.show_previous, help='Show previous image', disabled=state)
			with c2:
				# Delete
				state = flen == 0
				st.button('Delete', on_click=self.delete_image, help='Delete current image', disabled=state)
			with c3:
				# Next
				state = self.file_index == len(self.files) - 1 or flen == 0
				st.button('Next', on_click=self.show_next, help='Show next image', disabled=state)

		with tab2:
			st.header("Prompts")

		with tab3:
			st.header("Gallery")

if __name__ == '__main__':
    mv = GenerateView()
    mv.create_ui()