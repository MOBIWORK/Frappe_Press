<template>
	<Dialog
		:options="{
			title: 'Chỉnh sửa tiêu đề',
			actions: [
				{
					label: 'Cập nhật',
					variant: 'solid',
					loading: $resources.editTitle.loading,
					onClick: () => $resources.editTitle.submit()
				}
			]
		}"
		v-model="show"
	>
		<template v-slot:body-content>
			<FormControl label="Title" type="text" v-model="serverTitle" />
			<ErrorMessage class="mt-4" :message="$resources.editTitle.error" />
		</template>
	</Dialog>
</template>
<script>
export default {
	name: 'EditServerTitleDialog',
	props: ['modelValue', 'server'],
	emits: ['update:modelValue'],
	data() {
		return {
			serverTitle: this.server.title
		};
	},
	resources: {
		editTitle() {
			return {
				url: 'press.api.server.rename',
				params: {
					name: this.server?.name,
					title: this.serverTitle
				},
				validate() {
					if (this.serverTitle === this.server?.title) {
						return 'Không có thay đổi trong tiêu đề máy chủ';
					}
				},
				onSuccess() {
					this.show = false;
					this.server.title = this.serverTitle;
				}
			};
		}
	},
	computed: {
		show: {
			get() {
				return this.modelValue;
			},
			set(value) {
				this.$emit('update:modelValue', value);
			}
		}
	}
};
</script>
