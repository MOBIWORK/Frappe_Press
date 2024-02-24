<template>
	<div>
		<label class="text-lg font-semibold"> {{ $t('Choose_a_hostname') }} </label>
		<p class="text-base text-gray-700">
			{{ $t('CreateCodeServerDialog_content_1') }}
		</p>
		<div class="mt-4 flex">
			<input
				class="form-input z-10 w-full rounded-r-none"
				type="text"
				:value="modelValue"
				placeholder="subdomain"
				@change="subdomainChange"
			/>
			<div class="flex items-center rounded-r bg-gray-100 px-4 text-base">
				.{{ domain }}
			</div>
		</div>
		<div class="mt-1">
			<div
				v-if="subdomainAvailable"
				class="text-sm text-green-600"
				role="alert"
			>
				{{ modelValue }}.{{ domain }} {{ $t('is_available') }}
			</div>
			<ErrorMessage :message="errorMessage" />
		</div>
	</div>
</template>
<script>
export default {
	name: 'Hostname',
	props: ['modelValue', 'domain'],
	emits: ['update:modelValue', 'error'],
	data() {
		return {
			subdomainAvailable: false,
			errorMessage: null
		};
	},
	methods: {
		async subdomainChange(e) {
			let subdomain = e.target.value;
			this.$emit('update:modelValue', subdomain);
			this.subdomainAvailable = false;

			let error = this.$validateSubdomain(subdomain);
			if (!error) {
				let subdomainTaken = await this.$call('press.api.spaces.exists', {
					subdomain,
					domain: this.domain
				});
				if (subdomainTaken) {
					error = `${subdomain}.${this.domain} ${this.$t('already_exists')}.`;
				} else {
					this.subdomainAvailable = true;
				}
			}
			this.errorMessage = error;
			this.$emit('error', error);
		}
	}
};
</script>
