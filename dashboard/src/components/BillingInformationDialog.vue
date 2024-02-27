<template>
	<Dialog
		:options="{ title: $t('BillingInformationDialog_content_1') }"
		v-model="showDialog"
	>
		<template v-slot:body-content>
			<StripeCard
				class="mb-1"
				@complete="
					showDialog = false;
					$emit('success');
				"
			/>
		</template>
	</Dialog>
</template>
<script>
import StripeCard from '@/components/StripeCard.vue';

export default {
	name: 'BillingInformationDialog',
	props: ['modelValue'],
	emits: ['update:modelValue', 'success'],
	components: {
		StripeCard
	},
	computed: {
		showDialog: {
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
