<template>
	<Dialog
		:options="{
			title: $t('Drop_Bench'),
			actions: [
				{
					label: $t('Drop_Bench'),
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
				{{ $t('BenchDropDialog_content_1') }}
			</p>
			<p class="mt-4 text-base">
				{{ $t('Please_type') }}
				<span class="font-semibold">{{ bench.title }}</span>
				{{ $t('to_confirm') }}.
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
						return this.$t('BenchDropDialog_content_2');
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
