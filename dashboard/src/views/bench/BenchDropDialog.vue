<template>
	<Dialog
		:options="{
			title: 'Xóa Bench',
			actions: [
				{
					label: 'Xóa Bench',
					variant: 'solid',
					theme: 'red',
					loading: $resources.dropBench.loading,
					onClick: () => $resources.dropBench.submit()
				}
			]
		}"
		v-model="show"
	>
		<template v-slot:body-content>
			<p class="text-base">
				Bạn có chắc chắn muốn xóa bỏ bench này không? Tất cả các tổ chức trên
				bench này nên được xóa bỏ thủ công trước khi xóa bench. Hành động này
				không thể được hoàn tác.
			</p>
			<p class="mt-4 text-base">
				Vui lòng nhập
				<span class="font-semibold">{{ bench.title }}</span> để xác nhân.
			</p>
			<FormControl class="mt-4 w-full" v-model="confirmBenchName" />
			<ErrorMessage class="mt-2" :message="$resources.dropBench.error" />
		</template>
	</Dialog>
</template>
<script>
export default {
	name: 'EditBenchTitleDialog',
	props: ['modelValue', 'bench'],
	emits: ['update:modelValue'],
	data() {
		return {
			confirmBenchName: ''
		};
	},
	resources: {
		dropBench() {
			return {
				url: 'press.api.bench.archive',
				params: {
					name: this.bench?.name
				},
				onSuccess() {
					this.show = false;
					this.$router.push('/sites');
				},
				validate() {
					if (this.bench?.title !== this.confirmBenchName) {
						return 'Vui lòng nhập tên bench để xác nhận';
					}
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
