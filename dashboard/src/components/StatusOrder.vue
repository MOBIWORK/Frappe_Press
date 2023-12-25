<template>
	<Badge
		:variant="'outline'"
		:theme="styleBadge[status]"
		size="lg"
		:label="description"
	>
	</Badge>
</template>

<script>
import { Badge } from 'frappe-ui';

export default {
	name: 'StatusOrder',
	props: ['status', 'description'],
	data() {
		return {
			styleBadge: {
				0: 'orange',
				1: 'green',
				2: 'red',
				3: 'gray'
			}
		};
	}
};
</script>
