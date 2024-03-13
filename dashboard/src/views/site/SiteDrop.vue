<template>
	<div class="shrink-0">
		<slot v-bind="{ showDialog }"></slot>
		<Dialog
			:options="{
				title: $t('Drop_Site'),
				actions: [
					{
						label: site.archive_failed
							? $t('Force_Drop_Site')
							: $t('Drop_Site'),
						variant: 'solid',
						theme: 'red',
						loading: $resources.dropSite.loading,
						onClick: () => $resources.dropSite.submit()
					}
				]
			}"
			v-model="dialogOpen"
		>
			<template v-slot:body-content>
				<p class="text-base">
					{{ $t('SiteDrop_content_1') }}
				</p>
				<p class="mt-4 text-base">
					{{ $t('Please_type') }}
					<span class="font-semibold">{{ site.name }}</span>
					{{ $t('to_confirm') }}.
				</p>
				<FormControl class="mt-4 w-full" v-model="confirmSiteName" />
				<div class="mt-4">
					<FormControl
						v-show="!site.archive_failed"
						id="auto-drop-checkbox"
						v-model="forceDrop"
						type="checkbox"
						label="Force"
					/>
				</div>
				<ErrorMessage class="mt-2" :message="$resources.dropSite.error" />
			</template>
		</Dialog>
	</div>
</template>

<script>
export default {
	name: 'SiteDrop',
	props: ['site'],
	data() {
		return {
			dialogOpen: false,
			confirmSiteName: null,
			forceDrop: false
		};
	},
	resources: {
		dropSite() {
			return {
				url: 'press.api.site.archive',
				params: {
					name: this.site?.name,
					force: this.site.archive_failed == true ? true : this.forceDrop
				},
				onSuccess() {
					this.dialogOpen = false;
					this.$router.push('/sites');
				},
				validate() {
					if (this.site?.name !== this.confirmSiteName) {
						return this.$t('Please_type_the_site_name_to_confirm');
					}
				}
			};
		}
	},
	methods: {
		showDialog() {
			this.dialogOpen = true;
		}
	}
};
</script>
