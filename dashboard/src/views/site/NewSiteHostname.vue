<template>
	<div>
		<label class="text-lg font-semibold"> {{ $t('Choose_a_hostname') }} </label>
		<p class="text-base text-gray-700">
			{{ $t('NewSiteHostname_content_1') }}
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
		<div class="mt-4">
			<div>
				<input
					id="checkrestore"
					name="checkrestore"
					label="ok"
					type="radio"
					class="form-radio text-gray-900"
					:checked="true"
					value="new"
					@change="checkRestoreChange"
				/>
				<label class="ml-2 text-base" for="checkrestore">{{
					$t('Create_new_data')
				}}</label>
			</div>
			<div class="mt-2">
				<input
					id="checkrestore1"
					name="checkrestore"
					label="ok"
					type="radio"
					value="restore"
					class="form-radio text-gray-900"
					@change="checkRestoreChange"
				/>
				<label class="ml-2 text-base" for="checkrestore1">
					{{ $t('Retrieve_old_data') }}</label
				>
			</div>
		</div>
	</div>
</template>
<script>
export default {
	name: 'Hostname',
	props: ['modelValue', 'checkRestore', 'checkRestore'],
	emits: ['update:modelValue', 'error', 'update:checkRestore'],
	data() {
		return {
			subdomainAvailable: false,
			errorMessage: null
		};
	},
	resources: {
		domain() {
			return {
				url: 'press.api.site.get_domain',
				auto: true
			};
		}
	},
	computed: {
		domain() {
			return this.$resources.domain.data;
		}
	},
	methods: {
		checkRestoreChange(e) {
			this.$emit('update:checkRestore', e.target.value);
		},
		async subdomainChange(e) {
			let subdomain = e.target.value;
			this.$emit('update:modelValue', subdomain);
			this.subdomainAvailable = false;

			let error = this.$validateSubdomain(subdomain);
			if (!error) {
				let subdomainTaken = await this.$call('press.api.site.exists', {
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
