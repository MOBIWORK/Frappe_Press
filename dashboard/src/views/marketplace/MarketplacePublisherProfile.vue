<template>
	<div>
		<div v-if="publisherProfileInfo && !publisherProfileInfo.profile_created">
			<Alert title="Bạn chưa tạo hồ sơ của mình.">
				<template #actions>
					<Button variant="solid" @click="showEditDialog = true"> Tạo </Button>
				</template>
			</Alert>
		</div>

		<Button
			v-if="$resources.getPublisherProfileInfo.loading"
			:loading="true"
			loadingText="Đang tải..."
		></Button>

		<div class="grid grid-cols-1 gap-5 md:grid-cols-2">
			<PublisherProfileCard
				:showEditDialog="showEditDialog"
				:profileData="publisherProfileInfo"
				@profile-updated="$resources.getPublisherProfileInfo.fetch()"
			/>
			<PublisherPayoutInfoCard :profileData="publisherProfileInfo" />
		</div>
	</div>
</template>

<script>
import PublisherProfileCard from '@/components/marketplace/PublisherProfileCard.vue';
import PublisherPayoutInfoCard from '@/components/marketplace/PublisherPayoutInfoCard.vue';

export default {
	data() {
		return {
			showEditDialog: false
		};
	},
	resources: {
		getPublisherProfileInfo() {
			return {
				url: 'press.api.marketplace.get_publisher_profile_info',
				auto: true
			};
		}
	},
	computed: {
		publisherProfileInfo() {
			if (
				this.$resources.getPublisherProfileInfo.loading ||
				!this.$resources.getPublisherProfileInfo.data
			) {
				return;
			}
			return this.$resources.getPublisherProfileInfo.data;
		}
	},
	components: { PublisherProfileCard, PublisherPayoutInfoCard }
};
</script>
